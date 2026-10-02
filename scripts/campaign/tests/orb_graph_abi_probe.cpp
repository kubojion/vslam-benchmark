// Small cross-library allocation/destruction check; no images or SLAM run.
#include "g2o/core/sparse_optimizer.h"
#include "g2o/types/types_six_dof_expmap.h"
int main() {
    for (int n = 0; n < 20; ++n) {
        g2o::SparseOptimizer graph;
        auto* vertex = new g2o::VertexSE3Expmap();
        vertex->setId(0);
        graph.addVertex(vertex);
        graph.clear();
    }
}
